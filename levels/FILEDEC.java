package ast;

import libs.TokenizedLine;
import ui.Main;
import java.util.ArrayList;

abstract class FILEDEC extends DEC {
    ArrayList<MEMBER> members = new ArrayList<>();
    String _extends = null;
    // I think these will largely be the same  be the same between abstract and class,lkjsadhflkajshdflkjashdflkjahsdkfljhas;dhflaksdjf

    public FILEDEC(TokenizedLine tokens) {
        super(tokens);
    }

    @Override
    public void parse() {
        System.out.println("Parsing " + this.name);
        if (this.tokens.checkNext(">")) {
            if (this.tokens.eof()) {
                this.kill("Failed inheritance");
            } else {
                this.tokens.pop(); // Consume ">";
                this._extends = tokens.pop();
            }
        }
        if (this.tokens.checkNext("(")) {
            this.parseMembers();
        }
        Main.symbolTable.put(this.name, this);
    }

    // I think these will largely be the same  be the same between abstract and class,
    // so we can put most of the functionality here and call super() plus any details.
    @Override
    public void validate() {

    }

    @Override
    public void evaluate() {

    }

    protected void parseMembers() {
        this.tokens.pop(); // Pop open brace
        boolean first = true;
        while (!this.tokens.peek().equals(")")) {
            if(!first) {
                if(this.tokens.checkNext(",")) {
                    this.tokens.pop();
                } else {
                    this.kill("Invalid member list");
                }
            }
            if (this.tokens.eof()) {
                this.kill("Reached eof parsing members");
            }
            MEMBER member = new MEMBER(tokens);
            member.parse();
            this.members.add(member);
            first = false;
        }
        this.tokens.pop(); // Pop close brace
    }
}
